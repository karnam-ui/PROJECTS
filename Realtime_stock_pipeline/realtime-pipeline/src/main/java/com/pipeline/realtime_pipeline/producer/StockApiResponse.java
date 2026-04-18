package com.pipeline.realtime_pipeline.producer;

//defining a class to represent the response we get from the stock API when we fetch live stock data. 
// This class will be used to deserialize the JSON response from the API into a Java object that we can work
//  with in our producer and other components of our pipeline.
import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StockApiResponse {

    @JsonProperty("Global Quote")
    private GlobalQuote globalQuote;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class GlobalQuote {
        @JsonProperty("01. symbol")
        private String symbol;

        @JsonProperty("05. price")
        private double price;

        @JsonProperty("09. change")
        private double change;

        @JsonProperty("10. change percent")
        private String changePercent;

        @JsonProperty("02. open")
        private double open;

        @JsonProperty("03. high")
        private double high;

        @JsonProperty("04. low")
        private double low;

        @JsonProperty("06. volume")
        private long volume;

        @JsonProperty("07. latest trading day")
        private String latestTradingDay;

        @JsonProperty("08. previous close")
        private double previousClose;
    }
}
