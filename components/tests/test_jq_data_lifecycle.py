from pyvider.conversion import marshal, unmarshal
from pyvider.cty import CtyDynamic
from pyvider.cty.conversion import cty_to_native

COMPLEX_INPUT_DATA = {
    "users": [{"name": "Alice"}, {"name": "Bob"}],
}

def test_full_marshal_unmarshal_function_argument_pipeline():
    # This test now correctly simulates the framework's behavior.
    # 1. Start with a native Python object.
    native_data = COMPLEX_INPUT_DATA
    # 2. Marshal it against a dynamic schema.
    dynamic_value_proto = marshal(native_data, schema=CtyDynamic())
    # 3. Unmarshal it back.
    unmarshaled_cty_value = unmarshal(dynamic_value_proto, schema=CtyDynamic())
    # 4. Convert back to native for comparison.
    final_native_arg = cty_to_native(unmarshaled_cty_value)
    assert final_native_arg == native_data
