package com.pipeline.realtime_pipeline.Repository;

import java.util.List;

import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.pipeline.realtime_pipeline.model.StockPrice;

@Repository
public interface StockPriceRepository extends JpaRepository<StockPrice, Long> {
    // Replaces: SELECT price, timestamp FROM stock_prices
    //           WHERE symbol=%s ORDER BY timestamp DESC LIMIT 100
    // Spring generates the SQL from the method name — no query needed
    List<StockPrice> findBySymbolOrderByTimestampDesc(String symbol, Pageable pageable);

    // Custom JPQL for the anomaly endpoint — last 50 rows across all symbols
    @Query("SELECT s FROM StockPrice s ORDER BY s.timestamp DESC")
    List<StockPrice> findRecent(Pageable pageable);

    // Gets the single latest price row per symbol — used in anomaly detection
    @Query("SELECT s FROM StockPrice s WHERE s.symbol = :symbol ORDER BY s.timestamp DESC")
    List<StockPrice> findLatestBySymbol(@Param("symbol") String symbol, Pageable pageable);
}
