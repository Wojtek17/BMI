-- filling blank adresses
SELECT h.ParcelID, h.propertyaddress,ho.ParcelID,ho.propertyaddress, COALESCE(h.propertyaddress,ho.propertyaddress) AS filled_address
FROM housing AS h
JOIN housing AS ho
ON h.ParcelID=ho.ParcelID and h.unique_id <>ho.unique_id
WHERE h.propertyaddress IS NULL

UPDATE housing 
SET propertyaddress = COALESCE(h.propertyaddress,ho.propertyaddress)
FROM housing AS h
JOIN housing AS ho
ON h.ParcelID=ho.ParcelID and h.unique_id <>ho.unique_id
WHERE h.propertyaddress IS NULL
