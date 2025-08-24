package com.dlyog.dl_creator.model;

import com.dlyog.dl_creator.Enum.LicenseStatusEnum;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Date;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Entity
@Table(name = "driving_license")
public class DrivingLicense {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    @Column(nullable = false, name = "id")
    private Long id;

    @OneToOne
    @JoinColumn(name = "user_id", referencedColumnName = "id", nullable = false)
    private User user;

    @Column(nullable = false, name = "first_name")
    private String firstName;

    @Column(nullable = false, name = "last_name")
    private String lastName;

    @Column(nullable = false, name = "license_number", unique = true)
    private String licenseNumber;

    @Column(nullable = false, name = "issue_date")
    private Date issueDate;

    @Column(nullable = false, name = "expiration_date")
    private Date expirationDate;

    @Column(nullable = false, name = "vehicle_type")
    private String vehicleType;

    @Column(name = "vehicle_make")
    private String vehicleMake;

    @Column(nullable = false, name = "address")
    private String address;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, name = "license_status")
    private LicenseStatusEnum licenseStatus;

}
