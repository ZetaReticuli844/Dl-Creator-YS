package com.dlyog.dl_creator.Auth.dto;

import lombok.Builder;
import lombok.Data;
import lombok.Getter;
import lombok.Setter;

@Builder
@Getter
@Setter
public class RegisterUserDto {
    private String email;

    private String password;

    private String fullName;


}