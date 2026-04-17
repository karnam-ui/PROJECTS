package com.pipeline.realtime_pipeline.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Data
@Setter //sometimes builder conflicts with all args constructor, so we need to add getter setter instead builder to work
@Getter
@AllArgsConstructor
@NoArgsConstructor
@Entity
@Table(name = "stock_price")
public class StockPrice {

    @Id
    @GeneratedValue(strategy=GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "symbol", nullable = false,length=10)
    private String symbol;

    @Column(name = "price", nullable = false)
    private double price;

    @Column(name = "open")
    private double open;

    @Column(name = "high")
    private double high;

    @Column(name = "low")
    private double low; 

    @Column(name = "change")
    private double change;

    @Column(name = "change_percent")
    private String changePercent;

    @Column(name = "timestamp", nullable = false)
    private long timestamp;

    @Column(name = "Volume")
    private long volume;

    @Column(name = "Latest_Trading_Day")
    private String latestTradingDay;

    @Column(name = "Previous_Close")
    private double previousClose;

    @Column(name = "Created_At")
    private long createdAt;

    @PrePersist 
    public void prePersist() {
        this.createdAt = System.currentTimeMillis();
    }
}
