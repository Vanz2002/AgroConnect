const {Product} = require('../models');
const controller = {};

controller.getAllProduct = async (req, res) => {
    try {
        const data = await Product.findAll({
            include: 'Category'
        });

        res.status(200).json({
            data: data
        });
    } catch (error) {
        res.status(404).json({
            message: error
        })
    }
}

controller.getProductById = async (req, res) => {

}

controller.createProduct = async (req, res) => {
    try {
        const {name, amount, location, crop_date, estimate_exp, category_id} = req.body;
        const newProduct = await Product.create({
            name: name,
            amount: amount,
            location: location,
            crop_date: crop_date,
            estimate_exp: estimate_exp,
            category_id:category_id
        });

        res.status(201).json({
            message: "New Product Created",
            data: newProduct
        })
    } catch (error) {
        res.status(404).json({
            message: error
        })
    }
}

controller.updateProduct = async (req, res) => {

}

controller.deleteProduct = async (req,res) => {
    
}


module.exports = controller;