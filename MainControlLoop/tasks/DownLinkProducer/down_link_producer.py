from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry
from MainControlLoop.lib.StateFieldRegistry import StateField


class DownLinkProducer:
    @staticmethod
    def create_dump(state_field_registry: StateFieldRegistry) -> str:
        """
        Creates a dump from the given state_field_registry.
        :param state_field_registry: A state field registry.
        :return: A formatted dump.
        """
        dump = "TJ:D;"

        # A list of elements to include in the dump
        # Will be included in the order specified
        elements = [StateField.TIME,
                    StateField.IIDIODE_OUT,
                    StateField.VIDIODE_OUT,
                    StateField.VPCM12V,
                    StateField.VPCM5V,
                    StateField.VPCM3V3,
                    StateField.VBCR1,
                    StateField.VBCR2,
                    StateField.VBCR33,
                    StateField.VSW3,
                    StateField.ISW3,
                    StateField.VSW4,
                    StateField.ISW4,
                    StateField.VSW6,
                    StateField.ISW6,
                    StateField.VSW7,
                    StateField.ISW7,
                    StateField.VSW8,
                    StateField.ISW8,
                    StateField.TLM_TBRD_DB,
                    StateField.PDM_3_STAT,
                    StateField.PDM_4_STAT,
                    StateField.PDM_6_STAT,
                    StateField.PDM_7_STAT,
                    StateField.PDM_8_STAT
                    ]

        for element in elements:
            value = state_field_registry.get(element)
            dump += f"{value};"

        return dump

    @staticmethod
    def create_beacon(state_field_registry: StateFieldRegistry) -> str:
        """
        Creates a beacon from the given state field registry
        :param state_field_registry: State field registry
        :return: A formatted beacon.
        """
        beacon = "TJ:B;"  # header

        # A list of elements to include in the beacon
        # Will be included in the order specified
        elements = [StateField.TIME,
                    StateField.IIDIODE_OUT,
                    StateField.VIDIODE_OUT,
                    StateField.VPCM12V,
                    StateField.VPCMBATV,
                    StateField.VPCM5V,
                    StateField.VPCM3V3,
                    StateField.VBCR1,
                    StateField.VBCR2,
                    StateField.VBCR33,
                    StateField.VSW3,
                    StateField.ISW3,
                    StateField.VSW4,
                    StateField.ISW4,
                    StateField.VSW6,
                    StateField.ISW6,
                    StateField.VSW7,
                    StateField.ISW7,
                    StateField.VSW8,
                    StateField.ISW8,
                    StateField.TLM_TBRD_DB,
                    StateField.PDM_3_STAT,
                    StateField.PDM_4_STAT,
                    StateField.PDM_6_STAT,
                    StateField.PDM_7_STAT,
                    StateField.PDM_8_STAT
                    ]

        for element in elements:
            value = state_field_registry.get(element)
            beacon += f"{value};"

        return beacon

    @staticmethod
    def create_response(state_field_registry: StateFieldRegistry, state_field: StateField) -> str:
        """
        Prepare a state field message. Detailed in 4.1.5.3 of documentation
        :param state_field_registry: State field registry
        :param state_field: State field to request for
        :return: A state field message
        """
        message = "TJ:S;"
        elements = [
            StateField.TIME,
            state_field
        ]

        for element in elements:
            value = state_field_registry.get(element)
            message += f"{element.value};"
            message += f"{value};"

        return message
