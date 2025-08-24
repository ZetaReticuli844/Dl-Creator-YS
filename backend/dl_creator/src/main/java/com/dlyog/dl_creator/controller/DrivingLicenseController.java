package com.dlyog.dl_creator.controller;

import com.dlyog.dl_creator.model.DrivingLicense;
import com.dlyog.dl_creator.record.ApiResponse;
import com.dlyog.dl_creator.record.DrivingLicenseRequest;
import com.dlyog.dl_creator.record.DrivingLicenseResponse;
import com.dlyog.dl_creator.record.DrivingLicenseUpdateRequest;
import com.dlyog.dl_creator.service.DrivingLicenseService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/drivingLicense")
public class DrivingLicenseController {
    @Autowired
    DrivingLicenseService drivingLicenseService;

    @PostMapping("/create")
    public ResponseEntity<?> createDrivingLicense(@RequestBody DrivingLicenseRequest drivingLicenseRequest) {
        DrivingLicenseResponse drivingLicense = drivingLicenseService.createDrivingLicense(drivingLicenseRequest);
        return ResponseEntity.ok(ApiResponse.<DrivingLicenseResponse>builder().
                success(true)
                .message("Driving license created successfully")
                .data(drivingLicense).build());
    }
    @GetMapping("/getLicenseDetails")
    public ResponseEntity<?> getDrivingLicense() {
        DrivingLicenseResponse drivingLicenseResponse = drivingLicenseService.getDrivingLicense();
        return ResponseEntity.ok(ApiResponse.<DrivingLicenseResponse>builder().
                success(true)
                .message("Driving license retrieved successfully")
                .data(drivingLicenseResponse).build());
    }

    @PostMapping("/updateStatus")
    public ResponseEntity<?> updateStatus(@RequestParam String status) {
        DrivingLicenseResponse drivingLicense = drivingLicenseService.updateStatus(status);
        return ResponseEntity.ok(ApiResponse.<DrivingLicenseResponse>builder().
                success(true)
                .message("Driving license status updated successfully")
                .data(drivingLicense).build());
    }

    @PostMapping("/updateLicenseInfo")
    public ResponseEntity<?> updateLicenseInfo(@RequestBody DrivingLicenseUpdateRequest drivingLicenseRequest) {
        DrivingLicenseResponse drivingLicense = drivingLicenseService.updateLicenseInfo(drivingLicenseRequest);
        return ResponseEntity.ok(ApiResponse.<DrivingLicenseResponse>builder().
                success(true)
                .message("Driving license info updated successfully")
                .data(drivingLicense).build());
    }

    @PostMapping("/changeAddress")
    public ResponseEntity<?> changeAddress(@RequestParam String address) {
        DrivingLicenseResponse drivingLicense = drivingLicenseService.changeAddress(address);
        return ResponseEntity.ok(ApiResponse.<DrivingLicenseResponse>builder().
                success(true)
                .message("Driving license address changed successfully")
                .data(drivingLicense).build());
    }
    @PostMapping("/renewLicense")
    public ResponseEntity<?> renewLicense() {
        DrivingLicenseResponse drivingLicense = drivingLicenseService.renewLicense();
        return ResponseEntity.ok(ApiResponse.<DrivingLicenseResponse>builder().
                success(true)
                .message("Driving license renewed successfully")
                .data(drivingLicense).build());
    }

}