// This class is responsible for fetching live stock prices from an external API (like Alpha Vantage) 
// and providing it to the StockDataProducer for sending to Kafka.
package com.pipeline.realtime_pipeline.producer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import com.pipeline.realtime_pipeline.model.StockData;

@Service
public class StockManager {

    @Value("${stock.api.key}")
    private String apiKey;//in application.properties

    private final RestTemplate restTemplate = new RestTemplate();//like fetch in JS to call external APIs

    public double getLivePrice(String symbol) {
        try {
            String url = buildUrl(symbol);

            StockApiResponse response =
                    restTemplate.getForObject(url, StockApiResponse.class);

            return extractPrice(response);

        } catch (RestClientException e) {
            throw new RuntimeException("Failed to fetch stock price", e);
        }
    }

    private String buildUrl(String symbol) {
        return "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=" + symbol + "&apikey=" + apiKey;
    }

    private double extractPrice(StockApiResponse response) {
        if (response == null || response.getGlobalQuote() == null) {
            throw new RuntimeException("Invalid API response");
        }
        return response.getGlobalQuote().getPrice();
    }

    public StockData getStockData(String symbol) {

        String url = buildUrl(symbol);

        StockApiResponse response =
                restTemplate.getForObject(url, StockApiResponse.class);

        if (response == null || response.getGlobalQuote() == null) {
            throw new RuntimeException("API limit hit or invalid response");
        }

        var quote = response.getGlobalQuote();

        return StockData.builder()
                .symbol(symbol)
                .price(quote.getPrice())
                .open(quote.getOpen())
                .high(quote.getHigh())
                .low(quote.getLow())
                .change(quote.getChange())
                .changePercent(quote.getChangePercent())
                .previousClose(quote.getPreviousClose())
                .latestTradingDay(quote.getLatestTradingDay())
                .volume((int) quote.getVolume())
                .timestamp(System.currentTimeMillis())
                .build();
    }
}
