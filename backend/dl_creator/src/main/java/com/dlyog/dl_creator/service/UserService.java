package com.dlyog.dl_creator.service;


import com.dlyog.dl_creator.dto.UserDto;
import com.dlyog.dl_creator.record.UserCreationRequest;

public interface UserService {
    UserDto createUser(UserCreationRequest user);
}
