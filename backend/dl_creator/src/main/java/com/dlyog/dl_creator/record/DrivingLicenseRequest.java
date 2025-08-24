package com.dlyog.dl_creator.record;

import jakarta.validation.constraints.*;

import java.util.Date;

public record DrivingLicenseRequest(



        @NotBlank(message = "First name is required")
        @Size(min = 2, max = 50, message = "First name must be between 2 and 50 characters")
        String firstName,

        @NotBlank(message = "Last name is required")
        @Size(min = 2, max = 50, message = "Last name must be between 2 and 50 characters")
        String lastName,



        @NotBlank(message = "Vehicle type is required")
        String vehicleType,

        String vehicleMake,

        @NotBlank(message = "Address is required")
        @Size(min = 5, max = 200, message = "Address must be between 5 and 200 characters")
        String address



) {}