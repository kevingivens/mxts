from mxts.core.data import Position

class StrategyManagerRiskMixin(object):
    
    # *********************
    # Risk Methods        *
    # *********************
    def risk(self, position: Position = None) -> str:  # TODO
        return self._risk_mgr.risk(position=position)
