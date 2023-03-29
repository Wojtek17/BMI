-- standarization of data
SELECT DISTINCT (soldasvacant), count(soldasvacant)
FROM housing
GROUP by soldasvacant

SELECT
CASE WHEN soldasvacant = 'N' THEN 'No'
ELSE 
CASE WHEN soldasvacant = 'Y' THEN 'Yes'
ELSE soldasvacant
END 
END AS soldasvacant
FROM housing
--WHERE soldasvacant ='N' OR soldasvacant='Y'

UPDATE housing 
SET soldasvacant = CASE WHEN soldasvacant = 'N' THEN 'No'
ELSE 
CASE WHEN soldasvacant = 'Y' THEN 'Yes'
ELSE soldasvacant
END 
END
