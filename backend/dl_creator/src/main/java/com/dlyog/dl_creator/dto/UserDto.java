package com.dlyog.dl_creator.dto;

import lombok.Builder;
import lombok.Data;
import lombok.Getter;
import lombok.Setter;

@Data
@Builder


public class UserDto {
    private String email;
    private String fullName;
}
