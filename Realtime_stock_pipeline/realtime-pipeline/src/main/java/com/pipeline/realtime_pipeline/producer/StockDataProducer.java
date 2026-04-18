package com.pipeline.realtime_pipeline.producer;

import java.util.List;
import java.util.Random;
import java.util.concurrent.CompletableFuture;

import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.SendResult;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import com.pipeline.realtime_pipeline.model.StockData;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;


@Slf4j //to enable logging in this class, which can be useful for debugging and monitoring the producer's activity
@Component //to indicate that this class is a Spring component, allowing it to be automatically detected and managed by the Spring framework
@RequiredArgsConstructor //to generate a constructor with required arguments, which can be useful for dependency injection


public class StockDataProducer {
    private final static String TOPIC = "stock-data"; //the name of the Kafka topic to which we will be sending stock data messages
    private final static List<String> STOCK_SYMBOLS = List.of("AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"); //a list of stock symbols that we will be simulating data for
    private final Random random = new Random(); //a Random instance to generate random stock data values

    private final KafkaTemplate<String, StockData> kafkaTemplate; //a service for sending messages to Kafka, which will be injected by Spring
    private final StockManager stockService; //StockService to fetch complete stock data
    
    @Scheduled(fixedRate = 2000) //to schedule the sendStockData method to run every 2 seconds, simulating real-time data generation

    public void produce(){
        String symbol = STOCK_SYMBOLS.get(random.nextInt(STOCK_SYMBOLS.size())); //randomly select a stock symbol from the list
        
        // Fetch complete stock data with all fields (price, open, high, low, change, etc.)
        StockData data = stockService.getStockData(symbol);

        // Send the generated stock data to the Kafka topic asynchronously
        CompletableFuture<SendResult<String, StockData>> future = kafkaTemplate.send(TOPIC, data.getSymbol(), data);
        future.whenComplete((result, ex) -> {
            if (ex != null) {
                log.error("Failed to send stock data: {}", ex.getMessage());
            } else {
                log.info("Sent stock data: {} to topic: {}", data, TOPIC);
            }
        });
            
    }
}

