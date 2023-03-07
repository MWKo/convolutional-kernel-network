import numpy as np
from layer_base import LayerBase
from gradient_calculation_info import GradientCalculationInfo

class PoolingLayer(LayerBase):
    def __init__(self, input_size, in_channels, pooling_size):
        super().__init__(
            input_size=input_size, 
            output_size=(input_size[0] // pooling_size[0], input_size[1] // pooling_size[1]), 
            in_channels=in_channels, 
            out_channels=in_channels
        )

        self._pooling_size = pooling_size
        self._last_output = None

    @property
    def pooling_size(self):
        return self._pooling_size

    @property
    def last_output(self):
        return self._last_output

    
    def compute_gradient(self, gradient_calculation_info):
        gci = gradient_calculation_info
        new_info = GradientCalculationInfo(
            last_output_after_pooling=gci.last_output_after_pooling, 
            U=gci.U, 
            U_upscaled=self.backward(gci.U_upscaled),
            layer_number=gci.layer_number - 1
        )
        return 0, new_info
    

    def gradient_descent(self, descent):
        pass


    def forward(self, input):
        self._last_output = self._avg_pooling(input)
        return self._last_output


    def backward(self, U):
        return self._avg_pooling_t(U)


    def _avg_pooling(self, U):
        assert U.shape[1] == self._input_size[0] * self._input_size[1]
        U_3d = np.reshape(U, (U.shape[0], self._input_size[0], self._input_size[1]))

        pooled_size = (U.shape[0], self._output_size[0], self._output_size[1])
        pooled = np.zeros(pooled_size)

        for x in range(self._pooling_size[0]):
            for y in range(self._pooling_size[1]):
                pooled += U_3d[:,   x : x + pooled_size[1] * self._pooling_size[0] : self._pooling_size[0], 
                                    y : y + pooled_size[2] * self._pooling_size[1] : self._pooling_size[1]]

        pooled /= self._pooling_size[0] * self._pooling_size[1]
        return pooled.reshape((pooled_size[0], pooled_size[1] * pooled_size[2]))


    def _avg_pooling_t(self, U):
        assert U.shape[1] == self._output_size[0] * self._output_size[1]
        U_3d = np.reshape(U, (U.shape[0], self._output_size[0], self._output_size[1]))

        upscaled_size = (U.shape[0], self._input_size[0], self._input_size[1])
        upscaled = np.empty(upscaled_size)

        for x in range(self._pooling_size[0]):
            for y in range(self._pooling_size[1]):
                upscaled[:, x : x + self._output_size[0] * self._pooling_size[0] : self._pooling_size[0], 
                            y : y + self._output_size[1] * self._pooling_size[1] : self._pooling_size[1]] = U_3d
        
        upscaled[:, self._output_size[0] * self._pooling_size[0]::, :] = 0
        upscaled[:, :, self._output_size[1] * self._pooling_size[1]::] = 0

        upscaled /= self._pooling_size[0] * self._pooling_size[1]
        return upscaled.reshape((upscaled_size[0], upscaled_size[1] * upscaled_size[2]))