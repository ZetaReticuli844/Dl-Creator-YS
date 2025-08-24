package com.dlyog.dl_creator.repository;

import com.dlyog.dl_creator.model.DrivingLicense;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

public interface DrivingLicenseJpa extends JpaRepository<DrivingLicense, Long> {

    @Query("SELECT d FROM DrivingLicense d WHERE d.user.id = ?1")
    DrivingLicense findByUserId(Integer userId);
}
