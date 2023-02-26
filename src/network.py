import numpy as np
import layer as lr
from internal_filter_layer import IntFilterLayer
from internal_pooling_layer import IntPoolingLayer
from gradient_calculation_info import GradientCalculationInfo

class Network:
    @staticmethod
    def create_random(input_size, in_channels, layers, output_nodes):
        int_layers = []
        for layer in layers:
            new_layer = layer.build(input_size, in_channels)
            input_size = new_layer.output_size
            in_channels = new_layer.out_channels

            int_layers.append(new_layer)
        
        output_weights = np.random.normal(0, 1 / np.sqrt(in_channels * input_size[0] * input_size[1]), 
                                        size=(output_nodes, in_channels, input_size[0] * input_size[1]))
        
        return Network(int_layers, output_weights)


    def __init__(self, int_layers, output_weights):
        self._layers = int_layers
        self.output_weights = output_weights

        self._last_output = None

    @property
    def input_size(self):
        return self._layers[0].input_size
    
    @property
    def output_size(self):
        return self.output_weights.shape[0]

    @property
    def layers(self):
        return self._layers
    
    def forward(self, x):
        for layer in self._layers:
            x = layer.forward(x)
            
        self._last_output = np.einsum('jk,ijk->i', x, self.output_weights)
        return self._last_output

    def gradients(self, loss_func, expected_output):
        # layers + output_weights
        gradients = [None] * (len(self._layers) + 1)

        loss_func_gradient = loss_func.gradient(self._last_output, expected_output)
        gradients[-1] = np.einsum('i,jk->ijk', loss_func_gradient, self._layers[len(self._layers) - 1].last_output)

        next_U = np.einsum('k,kij->ij', loss_func_gradient, self.output_weights)
        gci = GradientCalculationInfo(
            next_filter_layer_input=self._layers[len(self._layers) - 1].last_output,
            next_U=next_U,
            next_U_upscaled=next_U,
            layer_number=len(self._layers)-1
        )
        
        for i in reversed(range(len(self._layers))):
            gradients[i], gci = self._layers[i].compute_gradient(gci)
        
        return gradients