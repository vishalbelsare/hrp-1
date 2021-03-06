# pylint: disable=too-many-arguments, missing-module-docstring, missing-function-docstring
import numpy as np
import pandas as pd
from typing import Dict

from dataclasses import dataclass


def risk_parity(cluster_left, cluster_right, cov, node=None):
    # combine two clusters

    def parity(v_left, v_right):
        """
        Compute the weights for a risk parity portfolio of two assets
        :param v_left: Variance of the "left" portfolio
        :param v_right: Variance of the "right" portfolio
        :return: w, 1-w the weights for the left and the right portfolio.
                 It is w*v_left == (1-w)*v_right and hence w = v_right / (v_right + v_left)
        """
        return v_right / (v_left + v_right), v_left / (v_left + v_right)

    assert set(cluster_left.assets).isdisjoint(set(cluster_right.assets))

    # the split is such that v_left * alpha_left == v_right * alpha_right and alpha + beta = 1
    alpha_left, alpha_right = parity(cluster_left.variance, cluster_right.variance)

    # assets in the cluster are the assets of the left and right cluster further downstream
    assets = {**(alpha_left * cluster_left.weights).to_dict(),
              **(alpha_right * cluster_right.weights).to_dict()}

    weights = np.array(list(assets.values()))
    covariance = cov[assets.keys()].loc[assets.keys()]

    var = np.linalg.multi_dot((weights, covariance, weights))

    return Cluster(assets=assets, variance=var, left=cluster_left, right=cluster_right, node=node)


@dataclass(frozen=True)
class Cluster:
    """
    Clusters are the nodes of the graphs we build.
    Each cluster is aware of the left and the right cluster
    it is connecting to.
    """
    assets: Dict[str, float]
    variance: float
    node: object = None
    left: object = None
    right: object = None

    def __post_init__(self):
        assert self.variance > 0
        if self.left is None:
            # if there is no left, there can't be a right
            assert self.right is None
        else:
            # left is not None, hence both left and right have to be clusters
            assert isinstance(self.left, Cluster)
            assert isinstance(self.right, Cluster)
            assert set(self.left.assets.keys()).isdisjoint(set(self.right.assets.keys()))

    @property
    def is_leaf(self):
        return self.left is None and self.right is None

    @property
    def weights(self):
        return pd.Series(self.assets, name="Weights").sort_index()
