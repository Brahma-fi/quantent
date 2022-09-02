"""
This module allows us to calculate the values associated with position values for UniswapV3:
position value, delta and gamma.
"""
import numpy as np


class UniswapV3():  # pragma: no cover
    """
    Class implementing the models of values associated with the Uniswap V3:
    Position value function, Delta, Gamma.
    """

    def __init__(self, liquidity: float, initial_price: float, price_barriers: list):
        """
        Class constructor.

        :param liquidity: (float)
        :param initial_price: (float)
        :param price_barriers: (list)
        """

        self.initial_price = initial_price
        self.price_barriers = price_barriers
        self.liquidity_usd = liquidity
        self.liquidity = self.convert_liquidity(liquidity, initial_price)
        self.initial_quantity = self.calculate_initial_quantity()
        self.delta_e = self.delta_e_calculation()

    def convert_liquidity(self, liquidity, price):
        """
        TODO: COMMENT THE FUNCTION
        """
        usd_amount = liquidity
        prices = [price, 1]
        lower_limit, upper_limit = self.price_barriers
        price_token0, price_token1 = prices
        current_price = price_token0 / price_token1
        sqr_c = np.sqrt(current_price)
        sqr_l = np.sqrt(lower_limit)
        sqr_u = np.sqrt(upper_limit)

        if current_price <= lower_limit:
            liquidity = float(usd_amount / price_token0) * sqr_l * sqr_u / (sqr_u - sqr_l)
        elif current_price <= upper_limit:
            amounts_ratio = (sqr_c - sqr_l) * (sqr_u * sqr_c) / (sqr_u - sqr_c)
            amount0 = float(usd_amount) / ((amounts_ratio * price_token1) + price_token0)
            amount1 = amount0 * amounts_ratio
            liquidity = self.get_liquidity(amount0, amount1, current_price, upper_limit, lower_limit)
        else:
            liquidity = float(usd_amount / price_token1) / (sqr_u - sqr_l)

        return liquidity

    def calculate_initial_quantity(self) -> list:
        """
        Calculates the initial quantity of tokens from the provided liquidity and initial price.

        TODO: COMMENT THE FUNCTION

        :return: (list) List of the initial quantities.
        """

        # Assigning the values of the upper and lower price barriers for the given contract
        t_l, t_h = self.price_barriers

        # Calculating the initial token quantity for token X and token Y

        if self.initial_price <= t_l:

            x_0 = self.liquidity * self.delta_price_sqrt() / np.sqrt(np.prod(self.price_barriers))
            y_0 = 0

        elif self.initial_price >= t_h:

            x_0 = 0
            y_0 = self.liquidity * self.delta_price_sqrt()

        else:

            x_0 = self.liquidity * (np.sqrt(t_h) - np.sqrt(self.initial_price)) / np.sqrt(self.initial_price * t_h)
            y_0 = self.liquidity * (np.sqrt(self.initial_price) - np.sqrt(t_l))

        output = [x_0, y_0]

        return output

    @staticmethod
    def get_liquidity(amount_token0, amount_token1, current_price, upper_limit, lower_limit):
        """
        TODO: COMMENT THE FUNCTION
        """
        sqr_c = np.sqrt(current_price)
        sqr_l = np.sqrt(lower_limit)
        sqr_u = np.sqrt(upper_limit)

        if current_price <= lower_limit:
            liquidity = float(amount_token0) * sqr_l * sqr_u / (sqr_u - sqr_l)
        elif current_price <= upper_limit:
            liquidity0 = float(amount_token0) * (sqr_u * sqr_c) / (sqr_u - sqr_c)
            liquidity1 = float(amount_token1) / (sqr_c - sqr_l)
            liquidity = min(liquidity0, liquidity1)
        else:
            liquidity = float(amount_token1) / (sqr_u - sqr_l)

        return liquidity

    def delta_price_sqrt(self) -> float:
        """
        Calculates the delta between the square roots of the upper and lower prices.

        :return: (float) Delta between the square roots of the upper and lower prices
        """
        # Assigning the values of the upper and lower price barriers for the given contract
        t_l, t_h = self.price_barriers

        # Calculating the delta
        output = np.sqrt(t_h) - np.sqrt(t_l)

        return output

    def delta_e_calculation(self) -> float:
        """
        Calculates the value of helper function for the calculation of the Uniswap V3
        position value functions depending on the value of the initial price in relation
        with provided barriers.

        :return: (float) The value of delta_e helper function.
        """
        # Assigning the values for the further calculation

        x_0, y_0 = self.initial_quantity

        t_l, t_h = self.price_barriers

        p_0 = self.initial_price

        # Calculating the output based on the the value of p_0 in relation to [t_l, t_h]

        if t_l > p_0:
            output = x_0

        elif t_l < p_0 < t_h:

            output = (x_0 * np.sqrt(p_0 / t_l)
                      * (self.delta_price_sqrt())
                      / (np.sqrt(t_h) - np.sqrt(p_0)))
        else:

            output = y_0 / np.sqrt(t_l * t_h)

        return output

    def position_value(self, price: float) -> float:
        """
        Calculates the position value for the Uniswap V3 LP based on the provided price.

        :param price: Current token price.

        :return: The position value of the LP for Uniswap V3
        """
        # Assigning the upper and lower price barriers for the given contract
        t_l, t_h = self.price_barriers

        # Calculating the substitute value of the delta of the square roots of price barriers

        delta_prices = self.delta_price_sqrt()

        # Calculating the value of the position

        if price <= t_l:

            output = self.delta_e * price

        elif t_l < price < t_h:

            output = (self.delta_e
                      * (np.sqrt(t_l * t_h) * (np.sqrt(price) - np.sqrt(t_l)) / delta_prices
                         + np.sqrt(price * t_l) * (np.sqrt(t_h) - np.sqrt(price)) / delta_prices))
        else:

            output = self.delta_e * np.sqrt(t_l * t_h)

        return output

    def position_value_delta(self, price: float) -> float:
        """
        Calculates the delta of the position value for the Uniswap V3 LP based on the provided price.
        Delta is calculated as the first partial derivative from the position value function on price.

        :param price: Current token price

        :return: The delta of position value of the LP for Uniswap V3
        """

        # Assigning the upper and lower price barriers for the given contract
        t_l, t_h = self.price_barriers

        # Calculating the substitute value of the delta of the square roots of price barriers

        delta_prices = self.delta_price_sqrt()

        # Calculating the delta

        if price <= t_l:

            output = self.delta_e

        elif t_l < price < t_h:

            output = (self.delta_e
                      * (np.sqrt(t_l / price) * (np.sqrt(t_h) - np.sqrt(price)) / delta_prices))
        else:

            output = 0

        return output

    def position_value_gamma(self, price: float) -> float:
        """
        Calculates the gamma of the position value for the Uniswap V3 LP based on the provided price.
        Gamma is calculated as the second partial derivative from the position value function on price.

        :param price: Current token price

        :return: The gamma of position value of the LP for Uniswap V3
        """

        # Assigning the upper and lower price barriers for the given contract
        t_l, t_h = self.price_barriers

        # Calculating the substitute value of the delta of the square roots of price barriers

        delta_prices = self.delta_price_sqrt()

        # Calculating the gamma

        if t_l < price < t_h:

            output = -(self.delta_e
                       * (np.sqrt(t_l * t_h) / (2 * np.sqrt(price) ** 3 * delta_prices)))
        else:

            output = 0

        return output

    def calc_naive_straddle_hedge(self):
        """
        TODO: COMMENT THE FUNCTION
        """
        initial_delta = self.initial_quantity[0]

        spot = self.initial_price
        upper_bound = self.price_barriers[1]
        call_slope = -initial_delta
        loss_at_bound = self.position_value(upper_bound) - self.liquidity_usd - initial_delta * (upper_bound - spot)
        call_intercept = loss_at_bound - call_slope * upper_bound
        call_strike = -call_intercept / call_slope
        call_qty = -call_slope

        lower_bound = self.price_barriers[0]
        put_slope = self.position_value_delta(lower_bound) - initial_delta
        loss_at_bound = self.position_value(lower_bound) - self.liquidity_usd - initial_delta * (lower_bound - spot)
        put_intercept = loss_at_bound - put_slope * lower_bound
        put_strike = -put_intercept / put_slope
        put_qty = put_slope

        return call_qty, call_strike, put_qty, put_strike
    
    def perp_position_pnl(self, price: float) -> float:
        
        initial_delta = -self.position_value_delta(self.initial_price)
        
        lp_pnl = self.position_value(price) - self.liquidity_usd
        loan_pnl = initial_delta * (price - self.initial_price)
        
        perp_position_value = loan_pnl + lp_pnl
        
        return perp_position_value
    
    
    def perp_position_delta(self, price: float) -> float:
        
        initial_delta = -self.position_value_delta(self.initial_price)
        
        lp_delta = self.position_value_delta(price)
        
        perp_position_delta = initial_delta + lp_delta
        
        return perp_position_delta
        
