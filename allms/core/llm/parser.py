from .response import LLMResponseModel


class LLMResponseParser:
    """ Parser class for parsing LLM responses """

    @classmethod
    def parse(cls, response: str) -> LLMResponseModel:
        # Note: I know this is not the best way to do things, but getting structured outputs CONSISTENTLY without
        # any error from the LLM is a pain in the fvck1ng @5s. It's better to just define your own SIMPLE custom text schema and
        # parse it manually instead of enforcing structured JSON outputs from the LLM via a third party library like
        # instructor -- I had enough of debugging and trying to fix the errors raised from it.
        # This method might need changes if the response output schema is changed in ./prompt.py -- ensure it is up-to-date
        parser_map = {
            # Note: Ensure this is consistent with the output schema
            # Also it must match with the response model
            # Format -- key_in_LLM_output: key_in_response_model
            "MESSAGE":            "message",
            "INTENT":             "intent",
            "SEND_TO":            "send_to",
            "SUSPECT_ID":         "suspect",
            "SUSPECT_CONFIDENCE": "suspect_confidence",
            "REASON_FOR_SUSPECT": "suspect_reason",
            "START_A_VOTE":       "start_a_vote",
            "VOTING_FOR":         "voting_for",
            "CHAT_SUMMARY":       "chat_summary"
        }
        response_dict = {}
        lines = response.splitlines()
        keys = set(parser_map.keys())

        for line in lines:
            # Skip empty lines if any (the LLM may output these -- who knows)
            line = line.strip()
            if not line:
                continue

            # Skip all the lines that don't have the required message
            line_key = line.split(":")[0].strip()
            if line_key not in keys:
                continue

            try:
                key, contents = line.split(":", maxsplit=1)
                key = key.strip()
                if key not in parser_map:
                    raise KeyError(f"Given key={key} is not supported")

                LLMResponseParser.__add_to_result(parser_map[key], contents, result=response_dict)

            except KeyError as ke:
                supp_keys = " ".join(list(parser_map.keys()))
                raise ValueError(f"{ke}. Supported keys: {supp_keys}. DOES NOT MATCH THE OUTPUT SCHEMA")
            except Exception as ex:
                raise ValueError(f"{ex}. Doesn't match the requested output schema")

        # Let pydantic do all the type checking and validation
        return LLMResponseModel(**response_dict)

    @staticmethod
    def __add_to_result(key: str, contents: str, result: dict[str, str]) -> None:
        parsed_contents = contents.strip()
        parsed_contents = parsed_contents.lstrip('"')
        parsed_contents = parsed_contents.rstrip('"')

        # Manually handle cases for None, True, False and integers
        pc = parsed_contents.lower()
        if pc == "none":
            parsed_contents = None
        elif pc == "true":
            parsed_contents = True
        elif pc == "false":
            parsed_contents = False
        elif pc.isnumeric():
            parsed_contents = int(pc)

        if key not in result:
            result[key] = parsed_contents
