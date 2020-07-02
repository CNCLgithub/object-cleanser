from arguments import opts
from cleanShapes import Clean
opt = opts().parse()


clean = Clean(opt=opt)
clean.cleanShapes()