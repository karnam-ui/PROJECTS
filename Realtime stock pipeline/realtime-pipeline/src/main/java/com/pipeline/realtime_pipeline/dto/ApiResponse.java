package com.pipeline.realtime_pipeline.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class ApiResponse<T> {
        private T data;
        private String Status;
        
        public static <T> ApiResponse<T> ok(T data) {
            return new ApiResponse<>(data, "ok");
        }
    
        public static <T> ApiResponse<T> error(String errorMessage) {
            return new ApiResponse<>(null, "error: " + errorMessage);
        }
}
