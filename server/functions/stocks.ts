const User = require('../src/models/user.model').default; // Adjust if using TypeScript
const { fetchStockData, fetchHistoricalStockData, searchStocks } = require('../src/utils/requests');
const yahooFinance = require('yahoo-finance2');

const getInfo = async (event) => {
    const symbol = event.pathParameters.symbol;

    try {
        const quote = await fetchStockData(symbol);
        return {
            statusCode: 200,
            body: JSON.stringify(quote),
        };
    } catch (error) {
        console.error("Error fetching " + symbol + " stock data:", error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: `Error fetching ${symbol} stock data: ${error.message}` }),
        };
    }
};

const getHistorical = async (event) => {
    const symbol = event.pathParameters.symbol;
    const period = event.queryStringParameters.period;

    try {
        const historicalData = await fetchHistoricalStockData(symbol, period);
        return {
            statusCode: 200,
            body: JSON.stringify(historicalData),
        };
    } catch (error) {
        console.error("Error fetching " + symbol + " stock data:", error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: `Error fetching ${symbol} stock data: ${error.message}` }),
        };
    }
};

const buyStock = async (event) => {
    const symbol = event.pathParameters.symbol;
    const { quantity, userId } = JSON.parse(event.body);

    try {
        const data = await fetchStockData(symbol);
        const price = data.regularMarketPrice;

        let user = await User.findById(userId);
        if (!user) {
            return {
                statusCode: 404,
                body: JSON.stringify({ message: "User not found" }),
            };
        }

        if (user.cash < price * quantity) {
            return {
                statusCode: 400,
                body: JSON.stringify({ message: "Not enough cash" }),
            };
        }

        user.cash -= price * quantity;

        // Add buy transaction to ledger
        user.ledger.push({
            symbol,
            price,
            quantity,
            type: "buy",
            date: Date.now(),
        });

        // Add position to user
        user.positions.push({
            symbol,
            quantity,
            purchasePrice: price,
            purchaseDate: Date.now(),
        });

        await user.save();
        return {
            statusCode: 200,
            body: JSON.stringify({ message: "Stock was bought successfully!" }),
        };
    } catch (error) {
        console.error("Error fetching " + symbol + " stock data:", error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: `Error fetching ${symbol} stock data: ${error.message}` }),
        };
    }
};

const sellStock = async (event) => {
    const symbol = event.pathParameters.symbol;
    let { quantity, userId } = JSON.parse(event.body); // Change `const` to `let`

    try {
        const data = await fetchStockData(symbol);
        const price = data.regularMarketPrice;

        let user = await User.findById(userId);
        if (!user) {
            return {
                statusCode: 404,
                body: JSON.stringify({ message: "User not found" }),
            };
        }

        // Check if user has enough shares to sell across all positions
        let quantityOwned = user.positions.reduce((total, position) => {
            return position.symbol === symbol ? total + position.quantity : total;
        }, 0);

        if (quantityOwned < quantity) {
            return {
                statusCode: 400,
                body: JSON.stringify({ message: "Not enough shares" }),
            };
        }

        user.cash += price * quantity;

        // Add sell transaction to ledger
        user.ledger.push({
            symbol,
            price,
            quantity,
            type: "sell",
            date: Date.now(),
        });

        // Sell quantity of shares
        for (let i = 0; i < user.positions.length; i++) {
            if (user.positions[i].symbol === symbol) {
                if (user.positions[i].quantity > quantity) {
                    user.positions[i].quantity -= quantity; // Adjust remaining quantity
                    break; // Exit the loop since we have sold the desired amount
                } else {
                    quantity -= user.positions[i].quantity; // Reduce the quantity needed to sell
                    user.positions.splice(i, 1); // Remove this position as we sold all shares
                    i--; // Adjust index after splice
                }
            }
        }

        await user.save();
        return {
            statusCode: 200,
            body: JSON.stringify({ message: "Stock was sold successfully!" }),
        };
    } catch (error) {
        console.error("Error fetching " + symbol + " stock data:", error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: `Error fetching ${symbol} stock data: ${error.message}` }),
        };
    }
};

const search = async (event) => {
    const query = event.pathParameters.query;

    if (!query) {
        return {
            statusCode: 400,
            body: JSON.stringify({ message: "No query provided" }),
        };
    }

    try {
        const quotes = await searchStocks(query);
        const stocksAndCurrencies = quotes.filter(quote => quote.quoteType && quote.quoteType !== "FUTURE" && quote.quoteType !== "Option");

        return {
            statusCode: 200,
            body: JSON.stringify(stocksAndCurrencies),
        };
    } catch (error) {
        console.error("Error searching stocks:", error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: error.message }),
        };
    }
};

// Exporting as named functions
exports.getInfo = getInfo;
exports.getHistorical = getHistorical;
exports.buyStock = buyStock;
exports.sellStock = sellStock;
exports.search = search;
