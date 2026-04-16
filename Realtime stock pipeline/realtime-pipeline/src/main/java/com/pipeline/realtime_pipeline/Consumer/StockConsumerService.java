package com.pipeline.realtime_pipeline.Consumer;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Service;

import com.pipeline.realtime_pipeline.Repository.StockPriceRepository;
import com.pipeline.realtime_pipeline.model.StockData;
import com.pipeline.realtime_pipeline.model.StockPrice;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@RequiredArgsConstructor
@Service
public class StockConsumerService {
    private final StockPriceRepository stockPriceRepository;

    @Autowired
    private StringRedisTemplate redisTemplate;

    @KafkaListener(topics = "stock-data", groupId = "stock-consumer-group")
    public void consume(@Payload StockData data,
                        @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
                        @Header(KafkaHeaders.OFFSET) long offset) {
        log.info("Consumed partition={}, offset={}, data={}", partition, offset, data);

        // Save to database
        StockPrice stockPrice = new StockPrice();
        stockPrice.setSymbol(data.getSymbol());
        stockPrice.setPrice(data.getPrice());
        stockPrice.setTimestamp(data.getTimestamp());
        stockPrice.setVolume(data.getVolume());
        stockPrice.setChange(data.getChange());
        stockPrice.setChangePercent(data.getChangePercent());
        stockPrice.setOpen(data.getOpen());
        stockPrice.setHigh(data.getHigh());
        stockPrice.setLow(data.getLow());

        stockPriceRepository.save(stockPrice);
        log.info("Saved stock price to database: {}", stockPrice);


        // Update Redis cache with latest price for the symbol
        String latestKey = "latest:" + data.getSymbol();
        redisTemplate.opsForValue().set(latestKey, String.valueOf(data.getPrice()));
    }
}


