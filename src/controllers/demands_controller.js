const {Demand} = require('../models');
const controller = {};

controller.getAllDemand = async (req, res) => {
    try {
        const data = await Demand.findAll({
            include: ['Category', 'User']
        });

        res.status(200).json({
            status: "Ok",
            message: "Success Get All Demands",
            data: data
        })
    } catch (error) {
        res.status(404).json({
            message: error
        })
    }
}

controller.getDemandById = async (req, res) => {
    try {
        const {demandId} = req.params;

        const data = await Demand.findByPk(demandId, {include: ['Category', 'User']});

        if (data === null){
            return res.status(404).json({
                status: "Not Found",
                message: `Data with id ${demandId} Not Found`
            });
        }

        res.status(200).json({
            status: "Ok",
            message: "Success Get a Demand",
            data: data
        });

    } catch (error) {
        res.status(404).json({
            message: error
        });
    }
}

controller.createDemand = async (req, res) => {
    try {
        // Check if Content-Type is set to JSON
        if (req.headers['content-type'] !== 'application/json') {
            return res.status(400).json({ 
                error: 'Invalid content type. Only JSON is supported.' 
            });
        }

        const {name, amount, location, category_id} = req.body;

        const newDemand = await Demand.create({
            name: name,
            amount: amount,
            location: location,
            category_id: category_id,
            user_id: req.user.user_id
        })

        return res.status(201).json({
            status: "Created",
            message: "New Demand Created",
            data: newDemand
        })

    } catch (error) {
        
    }
}

controller.updateDemand = async (req, res) => {
    try {
        // Check if Content-Type is set to JSON
        if (req.headers['content-type'] !== 'application/json') {
            return res.status(400).json({ 
                error: 'Invalid content type. Only JSON is supported.' 
            });
        }

        const {demandId} = req.params;
        const {name, amount, location, category_id} = req.body;

        const oldDemand = await Demand.update({
            name: name,
            amount: amount,
            location: location,
            category_id: category_id,
            user_id: req.user.user_id
        },
        {
            where: {
                id: demandId
            }
        });

        if (oldDemand[0] === 1) {
            res.status(200).json({
                status: "Ok",
                message: "Success Update Demand"
            })
        } else {
            res.status(404).json({
                status: "Not Found",
                message: "Demand Not Found"
            })
        }

    } catch (error) {
        res.status(404).json({
            message: error
        });
    }
}

controller.deleteDemand = async (req,res) => {
    try {
        const {demandId} = req.params;

        const rowsAffected = await Demand.destroy({
            where: {
                id: demandId
            }
        });

        if (rowsAffected > 0) {
            return res.status(200).json({
                status: "Ok",
                message: "Success Delete Demand"
            });
        } else {
            return res.status(404).json({
                status: "Not Found",
                message: "Demand Not Found"
            });
        }

    } catch (error) {
        res.status(404).json({
            message: error
        });
    }
}


module.exports = controller;