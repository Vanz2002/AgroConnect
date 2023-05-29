const router = require('express').Router();
const controller = require('../controllers/demands_controller');
const auth = require('../middleware/auth');

router.get('/', controller.getAllDemand);
router.get('/:demandId', controller.getDemandById);
router.post('/', auth, controller.createDemand);
router.put('/:demandId', auth, controller.updateDemand);
router.delete('/:demandId', auth, controller.deleteDemand);

module.exports = router;