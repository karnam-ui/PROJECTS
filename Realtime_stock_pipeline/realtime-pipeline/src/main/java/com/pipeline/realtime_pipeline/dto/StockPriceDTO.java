package com.pipeline.realtime_pipeline.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor

public class StockPriceDTO {
    private String stockSymbol;
    private double price;
    private long timestamp;
    private long volume;
    private double change;
    private String changePercent;
    private double open;
    private double high;
    private double low;
    private String latestTradingDay;
    private double previousClose;
    


    
    
}
