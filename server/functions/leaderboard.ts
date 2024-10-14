import { Handler } from '@netlify/functions';
import User from '../src/models/user.model'; // Adjust the path according to your structure
import { fetchStockData } from '../src/utils/requests'; // Adjust the path according to your structure

// Cache the leaderboard for 10 minutes
import NodeCache from 'node-cache';
const cache = new NodeCache({ stdTTL: 10 * 60 });

// Handler for the leaderboard endpoint
const getLeaderboard: Handler = async (event) => {
  /* 
  #swagger.tags = ['Leaderboard']
  */
  
  if (cache.has('leaderboard')) {
    const leaderboard = cache.get('leaderboard');
    return {
      statusCode: 200,
      body: JSON.stringify({ users: leaderboard }),
    };
  }

  try {
    const users = await getLeaderboardTopN(5);
    cache.set('leaderboard', users);
    return {
      statusCode: 200,
      body: JSON.stringify({ users }),
    };
  } catch (err) {
    return {
      statusCode: 500,
      body: JSON.stringify({ message: err.message }),
    };
  }
};

// Function to get top N users in the leaderboard
async function getLeaderboardTopN(
  n: number,
): Promise<{ username: string; value: number }[]> {
  try {
    // 1. Collate all unique stock symbols from users' positions using Aggregation
    const symbolsAggregation = await User.aggregate([
      { $unwind: '$positions' },
      { $group: { _id: '$positions.symbol' } },
    ]);

    const uniqueSymbols: string[] = symbolsAggregation.map((entry) => entry._id);

    // 2. Fetch stock prices in a single batch request
    const stockDataPoints = await Promise.all(
      uniqueSymbols.map((symbol) => fetchStockData(symbol)),
    );

    const stockPrices: { [key: string]: number } = {};
    stockDataPoints.forEach((dataPoint) => {
      stockPrices[dataPoint.symbol] = dataPoint.regularMarketPrice;
    });

    // 3. Compute portfolio values for each user using projection
    const usersWithPositions = await User.find(
      {},
      { username: 1, positions: 1, cash: 1 },
    );

    const userValues: { username: string; value: number }[] = [];
    usersWithPositions.forEach((user) => {
      let totalValue = user.cash;
      user.positions.forEach((position) => {
        const currentPrice = stockPrices[position.symbol];
        totalValue += currentPrice * position.quantity;
      });
      userValues.push({ username: user.username, value: totalValue });
    });

    // 4. Sort and pick top N users
    userValues.sort((a, b) => b.value - a.value);

    // Return only top N users
    return userValues.slice(0, n);
  } catch (error) {
    console.error("Error getting leaderboard:", error);
    throw new Error('Failed to retrieve leaderboard data'); // Ensure an error is thrown for handling
  }
}

// Exporting the handler
export { getLeaderboard };
