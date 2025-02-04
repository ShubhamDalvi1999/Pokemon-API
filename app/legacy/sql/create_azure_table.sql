CREATE TABLE pokemon (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL UNIQUE,
    types NVARCHAR(MAX),
    abilities NVARCHAR(MAX),
    moves NVARCHAR(MAX),
    stats NVARCHAR(MAX),
    height INT,
    weight INT
); 