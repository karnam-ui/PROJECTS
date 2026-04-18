
// src/main/java/com/pipeline/realtime_pipeline/config/KafkaConsumerConfig.java
package com.pipeline.realtime_pipeline.config;

import com.pipeline.realtime_pipeline.model.StockData;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory;
import org.springframework.kafka.core.ConsumerFactory;
import org.springframework.kafka.core.DefaultKafkaConsumerFactory;
import org.springframework.kafka.support.serializer.JsonDeserializer;

import java.util.HashMap;
import java.util.Map;

@EnableKafka        // activates @KafkaListener scanning — like @EnableScheduling for producers
@Configuration
public class KafkaConsumerConfig {

    @Value("${spring.kafka.bootstrap-servers}")
    private String bootstrapServers;

    @Bean
    public ConsumerFactory<String, StockData> consumerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG,  bootstrapServers);
        props.put(ConsumerConfig.GROUP_ID_CONFIG,           "stock-consumer-group");

        // how to read messages early vs late — LATEST skips old, EARLIEST replays all
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG,  "latest");

        // Key deserializer — reverse of producer's StringSerializer
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG,   StringDeserializer.class);

        // Value deserializer — reverse of producer's JsonSerializer
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, JsonDeserializer.class);

        // Trust our own package — without this JsonDeserializer rejects incoming messages
        props.put(JsonDeserializer.TRUSTED_PACKAGES, "com.pipeline.model");

        // Explicitly map the JSON to StockData — no type header needed
        props.put(JsonDeserializer.VALUE_DEFAULT_TYPE, StockData.class.getName());

        return new DefaultKafkaConsumerFactory<>(props);
    }

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, StockData>
            kafkaListenerContainerFactory() {

        ConcurrentKafkaListenerContainerFactory<String, StockData> factory =
                new ConcurrentKafkaListenerContainerFactory<>();

        factory.setConsumerFactory(consumerFactory());

        // Run 3 consumer threads in parallel — each owns a partition
        // Python had 1 thread — this is the Java upgrade
        factory.setConcurrency(3);

        return factory;
    }
}