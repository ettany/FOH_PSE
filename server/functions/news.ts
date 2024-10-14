import yahooFinance from "yahoo-finance2"; // Default import
import { Handler } from '@netlify/functions';

import dotenv from "dotenv";
dotenv.config();

const { SearchApi } = require("financial-news-api");
const searchApi = SearchApi(process.env.STOTRA_NEWSFILTER_API);

// Cache the results for 15 minutes
import NodeCache from "node-cache";
const cache = new NodeCache({ stdTTL: 15 * 60 });

// Handler for the news endpoint
const getNews: Handler = async (event) => {
  /* 
  #swagger.tags = ['News']
  */

  // Extracting the symbol from the path
  const symbol = event.path.split('/').pop() || ""; // Assumes symbol is the last segment of the path
  const symbolQuery = symbol !== "" ? "symbols:" + symbol + " AND " : "";

  if (cache.has(symbol + "-news")) {
    return {
      statusCode: 200,
      body: JSON.stringify(cache.get(symbol + "-news")),
    };
  }

  // If no API key for NewsFilter is provided, use Yahoo Finance API
  if (!process.env.STOTRA_NEWSFILTER_API) {
    console.warn("No NewsFilter API key provided. Using Yahoo Finance API.");
    try {
      const news = await yahooNews(symbol);
      return {
        statusCode: 200,
        body: JSON.stringify(news),
      };
    } catch (err) {
      console.log(err);
      return {
        statusCode: 500,
        body: JSON.stringify({ message: err.message }),
      };
    }
  }

  const query = {
    queryString:
      symbolQuery +
      "(source.id:bloomberg OR source.id:reuters OR source.id:cnbc OR source.id:wall-street-journal)",
    from: 0,
    size: 10,
  };

  try {
    const response = await searchApi.getNews(query);
    const news = response.articles.map((newsItem: any) => ({
      title: newsItem.title,
      publishedAt: newsItem.publishedAt,
      source: newsItem.source.name,
      sourceUrl: newsItem.sourceUrl,
      symbols: newsItem.symbols,
      description: newsItem.description,
    }));
    cache.set(symbol + "-news", news);
    return {
      statusCode: 200,
      body: JSON.stringify(news),
    };
  } catch (err: any) {
    if (err.response && err.response.data && err.response.data.message) {
      // Retry with Yahoo Finance API if Newsfilter quota is exceeded
      try {
        const news = await yahooNews(symbol);
        return {
          statusCode: 200,
          body: JSON.stringify(news),
        };
      } catch (err: any) {
        console.log(err);
        return {
          statusCode: 500,
          body: JSON.stringify({ message: err.message }),
        };
      }
    } else {
      console.log(err);
      return {
        statusCode: 500,
        body: JSON.stringify({ message: err.message }),
      };
    }
  }
};

// Function to fetch news from Yahoo Finance
async function yahooNews(symbol: string): Promise<any> {
  const options = {
    quotesCount: 0,
    newsCount: 10,
  };

  if (symbol === "") {
    symbol = "stock";
  }

  return yahooFinance
    .search(symbol || "", options)
    .then((response: any) => {
      const news = response.news.map((newsItem: any) => ({
        title: newsItem.title,
        publishedAt: newsItem.providerPublishTime,
        source: newsItem.publisher,
        sourceUrl: newsItem.link,
        symbols: newsItem.relatedTickers || [],
        description: "",
      }));

      cache.set(symbol + "-news", news);
      return news;
    })
    .catch((err: any) => {
      console.log(err);
      throw new Error(err);
    });
}

// Exporting the handler
export { getNews };
