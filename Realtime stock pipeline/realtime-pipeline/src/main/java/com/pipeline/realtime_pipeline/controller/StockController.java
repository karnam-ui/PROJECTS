package com.pipeline.realtime_pipeline.controller;

import java.util.List;
import java.util.Map;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.pipeline.realtime_pipeline.dto.ApiResponse;
import com.pipeline.realtime_pipeline.dto.StockPriceDTO;
import com.pipeline.realtime_pipeline.dto.StockService;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@RestController
@RequestMapping("/prices")           // all routes in this class start with /prices
@RequiredArgsConstructor
@CrossOrigin(origins = "*")          // allow Grafana (different port) to call this API
public class StockController {

    private final StockService stockService;  // injected — controller knows nothing about Redis or Postgres

    // ── GET /prices/latest ─────────────────────────────────────────────────
    // Returns: { "status": "ok", "data": { "AAPL": "182.45", "GOOGL": "140.10", ... } }
    // Replaces Python: @app.get("/prices/latest") def get_latest_prices()
    @GetMapping("/latest")
    public ResponseEntity<ApiResponse<Map<String, Double>>> getLatestPrices() {
        log.info("GET /prices/latest");
        Map<String, Double> prices = stockService.getLatestPrices();
        return ResponseEntity.ok(ApiResponse.ok(prices));
    }

    // ── GET /prices/history/{symbol} ───────────────────────────────────────
    // {symbol} is a path variable — /prices/history/AAPL, /prices/history/MSFT etc.
    // Returns: { "status": "ok", "data": [ { "symbol": "AAPL", "price": 182.45, ... }, ... ] }
    @GetMapping("/history/{symbol}")
    public ResponseEntity<ApiResponse<List<StockPriceDTO>>> getPriceHistory(
            @PathVariable String symbol     // extracts "AAPL" from the URL path
    ) {
        log.info("GET /prices/history/{}", symbol);

        // Validate the symbol before hitting the DB
        String upperSymbol = symbol.toUpperCase();
        List<StockPriceDTO> history = stockService.getPriceHistory(upperSymbol);
        return ResponseEntity.ok(ApiResponse.ok(history));
    }

    // ── GET /prices/anomalies ──────────────────────────────────────────────
    // Returns the 50 most recent price records — Grafana applies threshold to flag spikes
    @GetMapping("/anomalies")
    public ResponseEntity<ApiResponse<List<StockPriceDTO>>> getAnomalies() {
        log.info("GET /prices/anomalies");
        List<StockPriceDTO> recent = stockService.getRecentPrices();
        return ResponseEntity.ok(ApiResponse.ok(recent));
    }

    // ── GET /prices/health ─────────────────────────────────────────────────
    // Quick liveness check — Grafana can use this to verify the API is up
    @GetMapping("/health")
    public ResponseEntity<ApiResponse<String>> health() {
        return ResponseEntity.ok(ApiResponse.ok("pipeline running"));
    }
}