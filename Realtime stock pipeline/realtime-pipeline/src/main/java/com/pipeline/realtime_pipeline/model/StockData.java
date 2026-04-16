//defining a class to represent the stock data that we will be processing in our real-time pipeline.
// We will use Lombok annotations to reduce boilerplate code for getters, setters, constructors, and builders.
package com.pipeline.realtime_pipeline.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data   //auatomatic getters setters serialization and deserialization
@Builder //to create objects of this class using builder pattern without needing to write constructor
@NoArgsConstructor //to create a no-argument constructor, which is required for deserialization when reading from Kafka
@AllArgsConstructor //to create a constructor with all arguments, which can be useful for creating instances of StockData when needed USING Builder

public class StockData {
    private String symbol;
    private double price;
    private long timestamp;
    private int volume;
    private double change;
    private String changePercent;
    private double open;
    private double high;
    private double low;
    private String latestTradingDay;
    private double previousClose;

}
