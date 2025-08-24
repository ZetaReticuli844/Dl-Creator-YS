package com.dlyog.dl_creator.Auth.dto;



import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class LoginResponse {
    private String token;

    private long expiresIn;

    }