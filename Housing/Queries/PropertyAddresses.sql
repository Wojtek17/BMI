--Property Addresses

SELECT SUBSTRING(propertyaddress,1,POSITION(',' in propertyaddress)-1) AS address, SUBSTRING(propertyaddress,POSITION(',' in propertyaddress)+1,LENGTH(propertyaddress))
FROM housing

ALTER TABLE housing
ADD COLUMN PropertySplitAddress varchar(100)

UPDATE housing
SET PropertySplitAddress = SUBSTRING(propertyaddress,1,POSITION(',' in propertyaddress)-1)

ALTER TABLE housing
ADD COLUMN PropertySplitCity varchar(100)

UPDATE housing
SET PropertySplitCity = SUBSTRING(propertyaddress,POSITION(',' in propertyaddress)+1)

SELECT * FROM
housing
