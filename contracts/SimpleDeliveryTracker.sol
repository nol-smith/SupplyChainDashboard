// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleDeliveryTracker {
    struct Delivery {
        string deliveryId;
        int256 originLat;
        int256 originLon;
        int256 destLat;
        int256 destLon;
        string status;
        uint256 timestamp;
        int256 currentLat;
        int256 currentLon;
    }
    
    mapping(string => Delivery) public deliveries;
    
    // Add or update complete delivery
    function setDelivery(
        string memory _id,
        int256 _originLat,
        int256 _originLon,
        int256 _destLat,
        int256 _destLon,
        string memory _status,
        uint256 _timestamp,
        int256 _currentLat,
        int256 _currentLon
    ) public {
        deliveries[_id] = Delivery(_id, _originLat, _originLon, _destLat, _destLon, _status, _timestamp, _currentLat, _currentLon);
    }
    
    // Get complete delivery
    function getDelivery(string memory _id) public view returns (
        string memory,
        int256,
        int256,
        int256,
        int256,
        string memory,
        uint256,
        int256,
        int256
    ) {
        Delivery memory d = deliveries[_id];
        return (d.deliveryId, d.originLat, d.originLon, d.destLat, d.destLon, d.status, d.timestamp, d.currentLat, d.currentLon);
    }
    
    // Set status only
    function setStatus(string memory _id, string memory _status) public {
        deliveries[_id].status = _status;
    }
    
    // Get status only
    function getStatus(string memory _id) public view returns (string memory) {
        return deliveries[_id].status;
    }
    
    // Set current location only
    function setLocation(string memory _id, int256 _lat, int256 _lon) public {
        deliveries[_id].currentLat = _lat;
        deliveries[_id].currentLon = _lon;
    }
    
    // Get current location only
    function getLocation(string memory _id) public view returns (int256, int256) {
        return (deliveries[_id].currentLat, deliveries[_id].currentLon);
    }
}
