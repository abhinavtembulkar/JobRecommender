module.exports = (sequelize, DataTypes)=>{
    const User = sequelize.define("User",{
        firstname: {
            type: DataTypes.STRING,
            allowNull: false,
            validate:{
                notEmpty: true
            }
        },
        lastname: {
            type: DataTypes.STRING,
            allowNull: false,
            validate:{
                notEmpty: true
            }
        },
        email: {
            type: DataTypes.STRING,
            allowNull: false,
            primaryKey: true,
            validate:{
                notEmpty: true
            }
        },
        password: {
            type: DataTypes.STRING,
            allowNull: false,
            validate:{
                notEmpty: true
            }
        },
        isrecruiter:{
            type: DataTypes.STRING,
            defaultValue: false
        }
    })

    return User
}