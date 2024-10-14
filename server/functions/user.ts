import Position from "../src/models/position.model";
import User, { IUser } from "../src/models/user.model";
import { Request, Response } from "express";
import { fetchStockData } from "../src/utils/requests";

const getUserById = async (userId: string): Promise<IUser | null> => {
    return await User.findById(userId).lean();
};

const getLedger = async (req: Request, res: Response) => {
    /* 
    #swagger.tags = ['User Data']
    */
    try {
        const user = await getUserById(req.body.userId);
        if (!user) {
            return res.status(404).json({ message: "User not found" });
        }
        res.status(200).json({ ledger: user.ledger });
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
};

const getHoldings = async (req: Request, res: Response) => {
    /* 
    #swagger.tags = ['User Data']
    */
    try {
        const user = await getUserById(req.body.userId);
        if (!user) {
            return res.status(404).json({ message: "User not found" });
        }
        res.status(200).json({ positions: user.positions, cash: user.cash });
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
};

const getPortfolio = async (req: Request, res: Response) => {
    /* 
    #swagger.tags = ['User Data']
    */
    try {
        const user = await getUserById(req.body.userId);
        if (!user) {
            return res.status(404).json({ message: "User not found" });
        }

        let portfolioValue = 0;
        let portfolioPrevCloseValue = 0;

        const positionsNoDupes: { [key: string]: number } = {};
        user.positions.forEach((position) => {
            positionsNoDupes[position.symbol] = (positionsNoDupes[position.symbol] || 0) + position.quantity;
        });

        const symbols = Object.keys(positionsNoDupes);
        const quantities = Object.values(positionsNoDupes);

        const values = await Promise.all(symbols.map(fetchStockData));

        const listOfPositions = user.positions.map((position) => {
            const positionLiveData = values.find(value => value.symbol === position.symbol);
            if (positionLiveData) {
                portfolioValue += positionLiveData.regularMarketPrice * position.quantity;
                portfolioPrevCloseValue += positionLiveData.regularMarketPreviousClose * position.quantity;
                return {
                    ...position,
                    ...positionLiveData,
                };
            }
            return position; // Return original position if no live data
        });

        res.status(200).json({
            portfolioValue,
            portfolioPrevCloseValue,
            positions: listOfPositions,
            cash: user.cash,
        });
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
};

const getWatchlist = async (req: Request, res: Response) => {
    /* 
    #swagger.tags = ['User Watchlist']
    */
    try {
        const user = await getUserById(req.body.userId);
        if (!user) {
            return res.status(404).json({ message: "User not found" });
        }

        if (req.body.raw === "true") {
            return res.status(200).json({ watchlist: user.watchlist });
        }

        const values = await Promise.all(user.watchlist.map(fetchStockData));
        res.status(200).json({ watchlist: values });
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
};

const addToWatchlist = async (req: Request, res: Response) => {
    /* 
    #swagger.tags = ['User Watchlist']
    */
    try {
        const user = await getUserById(req.body.userId);
        if (!user) {
            return res.status(404).json({ message: "User not found" });
        }

        if (user.watchlist.includes(req.params.symbol)) {
            return res.status(400).json({ message: "Already in watchlist" });
        }

        user.watchlist.push(req.params.symbol);
        await user.save();
        res.status(200).json({ message: "Added to watchlist" });
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
};

const removeFromWatchlist = async (req: Request, res: Response) => {
    /* 
    #swagger.tags = ['User Watchlist']
    */
    try {
        const user = await getUserById(req.body.userId);
        if (!user) {
            return res.status(404).json({ message: "User not found" });
        }

        if (!user.watchlist.includes(req.params.symbol)) {
            return res.status(400).json({ message: "Not in watchlist" });
        }

        user.watchlist = user.watchlist.filter(symbol => symbol !== req.params.symbol);
        await user.save();
        res.status(200).json({ message: "Removed from watchlist" });
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
};

export default {
    getLedger,
    getHoldings,
    getPortfolio,
    getWatchlist,
    addToWatchlist,
    removeFromWatchlist,
};
