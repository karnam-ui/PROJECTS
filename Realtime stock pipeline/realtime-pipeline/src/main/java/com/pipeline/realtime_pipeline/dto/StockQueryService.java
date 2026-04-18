package com.pipeline.realtime_pipeline.dto;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.springframework.data.domain.PageRequest;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import com.pipeline.realtime_pipeline.repository.StockPriceRepository;

import lombok.Builder;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Builder
@Service
@RequiredArgsConstructor
public class StockQueryService {

    private static final List<String> SYMBOLS = List.of("AAPL", "GOOGL", "MSFT", "AMZN");

    private final StringRedisTemplate  redis;      // for /prices/latest  — hot cache
    private final StockPriceRepository stockRepo;  // for /prices/history — persistent store

    // ── Endpoint 1: /prices/latest ─────────────────────────────────────────
    // Reads from Redis — sub-millisecond, doesn't touch Postgres at all
    public Map<String, Double> getLatestPrices() {
        return SYMBOLS.stream()
                .collect(Collectors.toMap(
                        symbol -> symbol,                                          
                        symbol -> {
                            String val = redis.opsForValue().get("latest:" + symbol);
                                return val != null ? Double.parseDouble(val) : null;            
                        }
                ));
    }

    // ── Endpoint 2: /prices/history/{symbol} ───────────────────────────────
    // Queries Postgres via JPA — last 100 rows for the given symbol
    // Replaces Python: SELECT price, timestamp FROM stock_prices
    //                  WHERE symbol=%s ORDER BY timestamp DESC LIMIT 100
    public List<StockPriceDTO> getPriceHistory(String symbol) {
        return stockRepo
                .findBySymbolOrderByTimestampDesc(symbol, PageRequest.of(0, 100))
                .stream()
                .map(entity -> StockPriceDTO.builder()
                        .stockSymbol(entity.getSymbol())
                        .price(entity.getPrice())
                        .volume(entity.getVolume())
                        .timestamp(entity.getTimestamp())
                        .low(entity.getLow())
                        .high(entity.getHigh())
                        .open(entity.getOpen())
                        .change(entity.getChange())
                        .changePercent(
                        entity.getChangePercent() != null ? entity.getChangePercent() : "0%")
                        .build())
                .collect(Collectors.toList());
    }

    // ── Endpoint 3: /anomalies ─────────────────────────────────────────────
    // Returns the 50 most recent rows across all symbols — controller/Grafana
    // filters for spikes. Keeps the service layer simple — no anomaly logic here.
    // Replaces Python: SELECT symbol, price, timestamp FROM stock_prices
    //                  ORDER BY timestamp DESC LIMIT 50
    public List<StockPriceDTO> getRecentPrices() {
        return stockRepo
                .findRecent(PageRequest.of(0, 50))
                .stream()
                .map(entity -> StockPriceDTO.builder()
                        .stockSymbol(entity.getSymbol())
                        .price(entity.getPrice())
                        .volume(entity.getVolume())
                        .timestamp(entity.getTimestamp())
                        .low(entity.getLow())
                        .high(entity.getHigh())
                        .open(entity.getOpen())
                        .change(entity.getChange())
                        .changePercent(entity.getChangePercent())
                        .latestTradingDay(entity.getLatestTradingDay())
                        .previousClose(entity.getPreviousClose())
                        .build())
                .collect(Collectors.toList());
    }
}