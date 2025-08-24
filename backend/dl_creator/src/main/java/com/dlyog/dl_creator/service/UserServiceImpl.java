package com.dlyog.dl_creator.service;

import com.dlyog.dl_creator.dto.UserDto;
import com.dlyog.dl_creator.model.User;
import com.dlyog.dl_creator.record.UserCreationRequest;
import com.dlyog.dl_creator.repository.UserJpa;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Date;

@Service
public class UserServiceImpl implements UserService {
@Autowired UserJpa userJpa;
@Autowired PasswordEncoder passwordEncoder;

    @Override
    public UserDto createUser(UserCreationRequest user) {
        User user1 = User.builder()
                .email(user.email())
                .fullName(user.fullName())
                .password(passwordEncoder.encode(user.password()))
                .createdAt(new Date())
                .build();
        userJpa.save(user1);
        return UserDto.builder()
                .email(user.email())
                .fullName(user.fullName())
                .build();
    }

}
