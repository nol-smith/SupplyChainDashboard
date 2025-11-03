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
        uint256 expectedDeliveryDate;
        uint256 actualDeliveryDate;
    }
    
    struct StatusUpdate {
        string status;
        uint256 timestamp;
        string reason;
    }
    
    struct LocationUpdate {
        int256 lat;
        int256 lon;
        uint256 timestamp;
    }
    
    mapping(string => Delivery) public deliveries;
    mapping(string => StatusUpdate[]) public statusHistory;
    mapping(string => LocationUpdate[]) public locationHistory;
    
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
        int256 _currentLon,
        uint256 _expectedDeliveryDate
    ) public {
        deliveries[_id] = Delivery(_id, _originLat, _originLon, _destLat, _destLon, _status, _timestamp, _currentLat, _currentLon, _expectedDeliveryDate, 0);
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
        int256,
        uint256,
        uint256
    ) {
        Delivery memory d = deliveries[_id];
        return (d.deliveryId, d.originLat, d.originLon, d.destLat, d.destLon, d.status, d.timestamp, d.currentLat, d.currentLon, d.expectedDeliveryDate, d.actualDeliveryDate);
    }
    
    // Set status only
    function setStatus(string memory _id, string memory _status, string memory _reason) public {
        deliveries[_id].status = _status;
        // Auto-set actual delivery date when marked as delivered
        if (keccak256(bytes(_status)) == keccak256(bytes("Delivered")) && deliveries[_id].actualDeliveryDate == 0) {
            deliveries[_id].actualDeliveryDate = block.timestamp;
        }
        // Add to history
        statusHistory[_id].push(StatusUpdate(_status, block.timestamp, _reason));
    }
    
    // Get status only
    function getStatus(string memory _id) public view returns (string memory) {
        return deliveries[_id].status;
    }
    
    // Set current location only
    function setLocation(string memory _id, int256 _lat, int256 _lon) public {
        deliveries[_id].currentLat = _lat;
        deliveries[_id].currentLon = _lon;
        // Add to history
        locationHistory[_id].push(LocationUpdate(_lat, _lon, block.timestamp));
    }
    
    // Get current location only
    function getLocation(string memory _id) public view returns (int256, int256) {
        return (deliveries[_id].currentLat, deliveries[_id].currentLon);
    }
    
    // Get status history
    function getStatusHistory(string memory _id) public view returns (StatusUpdate[] memory) {
        return statusHistory[_id];
    }
    
    // Get location history
    function getLocationHistory(string memory _id) public view returns (LocationUpdate[] memory) {
        return locationHistory[_id];
    }
    
    // Get history counts
    function getStatusHistoryCount(string memory _id) public view returns (uint256) {
        return statusHistory[_id].length;
    }
    
    function getLocationHistoryCount(string memory _id) public view returns (uint256) {
        return locationHistory[_id].length;
    }
}
