// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract WarehouseContract {
    struct Warehouse {
        uint id;
        string name;
        string location;
        uint256 area;
        uint256 rentalPrice;
        address owner;
    }

    struct Lease {
        uint id;
        uint warehouseId;
        address tenant;
        uint256 rentalAmount;
        uint256 startDate;
        uint256 endDate;
    }

    mapping(uint => Warehouse) public warehouses;
    mapping(uint => Lease) public leases;
    uint public warehouseCount;
    uint public leaseCount;

    event WarehouseAdded(uint id, string name, string location, uint256 area, uint256 rentalPrice, address owner);
    event LeaseCreated(uint id, uint warehouseId, address tenant, uint256 rentalAmount, uint256 startDate, uint256 endDate);

    function addWarehouse(string memory _name, string memory _location, uint256 _area, uint256 _rentalPrice) public {
        warehouseCount++;
        warehouses[warehouseCount] = Warehouse(warehouseCount, _name, _location, _area, _rentalPrice, msg.sender);
        emit WarehouseAdded(warehouseCount, _name, _location, _area, _rentalPrice, msg.sender);
    }

    function createLease(uint _warehouseId, address _tenant, uint256 _rentalAmount, uint256 _startDate, uint256 _endDate) public {
        leaseCount++;
        leases[leaseCount] = Lease(leaseCount, _warehouseId, _tenant, _rentalAmount, _startDate, _endDate);
        emit LeaseCreated(leaseCount, _warehouseId, _tenant, _rentalAmount, _startDate, _endDate);
    }

    function getWarehouse(uint _id) public view returns (
        uint id,
        string memory name,
        string memory location,
        uint256 area,
        uint256 rentalPrice,
        address owner
    ) {
        require(_id > 0 && _id <= warehouseCount, "Invalid warehouse ID");
        Warehouse memory warehouse = warehouses[_id];
        return (
            warehouse.id,
            warehouse.name,
            warehouse.location,
            warehouse.area,
            warehouse.rentalPrice,
            warehouse.owner
        );
    }

    function getLease(uint _id) public view returns (
        uint id,
        uint warehouseId,
        address tenant,
        uint256 rentalAmount,
        uint256 startDate,
        uint256 endDate
    ) {
        require(_id > 0 && _id <= leaseCount, "Invalid lease ID");
        Lease memory lease = leases[_id];
        return (
            lease.id,
            lease.warehouseId,
            lease.tenant,
            lease.rentalAmount,
            lease.startDate,
            lease.endDate
        );
    }

    function getWarehouseCount() public view returns (uint) {
        return warehouseCount;
    }

    function getLeaseCount() public view returns (uint) {
        return leaseCount;
    }
}
