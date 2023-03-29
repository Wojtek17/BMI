--Removing duplicates
WITH CTE AS(SELECT *,
ROW_NUMBER() OVER(PARTITION BY parcelid, saledate, legalreference, propertyaddress,saleprice ORDER BY unique_id)
FROM housing
ORDER BY parcelid)

DELETE
FROM housing
WHERE parcelid IN (SELECT parcelid FROM
	   CTE
	   WHERE row_number>1)

SELECT * FROM CTE
WHERE row_number>1
