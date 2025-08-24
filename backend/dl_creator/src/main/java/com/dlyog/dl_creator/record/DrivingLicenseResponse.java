package com.dlyog.dl_creator.record;

import lombok.Builder;
import lombok.Data;

import java.util.Date;

@Builder
public record DrivingLicenseResponse(
        Long id,
        Integer userId,
        String licenseNumber,
        Date issueDate,
        Date expirationDate,
        String firstName,
        String lastName,
        String vehicleType,
        String vehicleMake,
        String address,
        String licenseStatus
) {
}
