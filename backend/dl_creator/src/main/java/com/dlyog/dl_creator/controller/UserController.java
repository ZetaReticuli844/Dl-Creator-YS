package com.dlyog.dl_creator.controller;

import com.dlyog.dl_creator.record.ApiResponse;
import com.dlyog.dl_creator.record.UserCreationRequest;
import com.dlyog.dl_creator.dto.UserDto;
import com.dlyog.dl_creator.model.User;
import com.dlyog.dl_creator.service.UserService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/user")
public class UserController {

    @Autowired
    private UserService userService;

    @GetMapping("/currentUser")
    public ResponseEntity<ApiResponse<UserDto>> getCurrentUser() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        User currentUser = (User) authentication.getPrincipal();

        UserDto dto = UserDto.builder()
                .email(currentUser.getEmail())
                .fullName(currentUser.getFullName())
                .build();

        return ResponseEntity.ok(ApiResponse.<UserDto>builder()
                .success(true)
                .message("Current user retrieved successfully")
                .data(dto)
                .build());
    }

    @PostMapping("/createUser")
    public ResponseEntity<ApiResponse<UserDto>> createUser(@Valid @RequestBody UserCreationRequest request) {
        UserDto createdUser = userService.createUser(request);

        return ResponseEntity.ok(ApiResponse.<UserDto>builder()
                .success(true)
                .message("User created successfully")
                .data(createdUser)
                .build());
    }
}
