// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract WarehouseRegistry {
    struct Warehouse {
        string name;
        string location;
        uint256 capacity;
        string facilities;
    }

    mapping(uint256 => Warehouse) public warehouses;
    uint256 public warehouseCount;

    event WarehouseAdded(uint256 id, string name, string location, uint256 capacity, string facilities);

    function addWarehouse(
        string memory _name,
        string memory _location,
        uint256 _capacity,
        string memory _facilities
    ) public {
        warehouseCount++;
        warehouses[warehouseCount] = Warehouse(_name, _location, _capacity, _facilities);
        emit WarehouseAdded(warehouseCount, _name, _location, _capacity, _facilities);
    }

    function getWarehouse(uint256 _id)
        public
        view
        returns (string memory, string memory, uint256, string memory)
    {
        Warehouse memory w = warehouses[_id];
        return (w.name, w.location, w.capacity, w.facilities);
    }
}
