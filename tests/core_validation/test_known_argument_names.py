import pytest

from graphql.core.language.location import SourceLocation
from graphql.core.validation.rules import KnownArgumentNames
from utils import expect_passes_rule, expect_fails_rule


def unknown_arg(arg_name, field_name, type_name, line, column):
    return {
        'message': KnownArgumentNames.message(arg_name, field_name, type_name),
        'locations': [SourceLocation(line, column)]
    }


def unknown_directive_arg(arg_name, directive_name, line, column):
    return {
        'message': KnownArgumentNames.unknown_directive_message(
            arg_name, directive_name),
        'locations': [SourceLocation(line, column)]
    }


def test_single_arg_is_known():
    expect_passes_rule(KnownArgumentNames, '''
        fragment argOnRequiredArg on Dog {
          doesKnowCommand(dogCommand: SIT)
        }
    ''')


def test_multiple_args_are_known():
    expect_passes_rule(KnownArgumentNames, '''
      fragment multipleArgs on ComplicatedArgs {
        multipleReqs(req1: 1, req2: 2)
      }
    ''')


def test_ignore_args_of_unknown_fields():
    expect_passes_rule(KnownArgumentNames, '''
      fragment argOnUnknownField on Dog {
        unknownField(unknownArg: SIT)
      }
    ''')


def test_multiple_args_in_reverse_order_are_known():
    expect_passes_rule(KnownArgumentNames, '''
      fragment multipleArgsReverseOrder on ComplicatedArgs {
        multipleReqs(req2: 2, req1: 1)
      }
    ''')


def test_no_args_on_optional_arg():
    expect_passes_rule(KnownArgumentNames, '''
      fragment noArgOnOptionalArg on Dog {
        isHousetrained
      }
    ''')


def test_args_are_known_deeply():
    expect_passes_rule(KnownArgumentNames, '''
      {
        dog {
          doesKnowCommand(dogCommand: SIT)
        }
        human {
          pet {
            ... on Dog {
                doesKnowCommand(dogCommand: SIT)
            }
          }
        }
      }
    ''')


def test_directive_args_are_known():
    expect_passes_rule(KnownArgumentNames, '''
      {
        dog @skip(if: true)
      }
    ''')


@pytest.mark.skipif(not hasattr(KnownArgumentNames,
                                "unknown_directive_message"),
                    reason=("KnownDirectives.unknown_directive_message not "
                            "yet implemented"))
def test_undirective_args_are_invalid():
    expect_fails_rule(KnownArgumentNames, '''
      {
        dog @skip(unless: true)
      }
    ''', [unknown_directive_arg('unless', 'skip', 3, 19)])


@pytest.mark.skipif(not hasattr(KnownArgumentNames, "message"),
                    reason="KnownArgumentNames.message not yet implemented")
def test_invalid_arg_name():
    expect_fails_rule(KnownArgumentNames, '''
      fragment invalidArgName on Dog {
        doesKnowCommand(unknown: true)
      }
    ''', [unknown_arg('unknown', 'doesKnowCommand', 'Dog', 3, 25)])


@pytest.mark.skipif(not hasattr(KnownArgumentNames, "message"),
                    reason="KnownArgumentNames.message not yet implemented")
def test_unknown_args_amongst_known_args():
    expect_fails_rule(KnownArgumentNames, '''
      fragment oneGoodArgOneInvalidArg on Dog {
        doesKnowCommand(whoknows: 1, dogCommand: SIT, unknown: true)
      }
    ''', [unknown_arg('whoknows', 'doesKnowCommand', 'Dog', 3, 25),
          unknown_arg('unknown', 'doesKnowCommand', 'Dog', 3, 55)])


@pytest.mark.skipif(not hasattr(KnownArgumentNames, "message"),
                    reason="KnownArgumentNames.message not yet implemented")
def test_unknown_args_deeply():
    expect_fails_rule(KnownArgumentNames, '''
      {
        dog {
          doesKnowCommand(unknown: true)
        }
        human {
          pet {
            ... on Dog {
              doesKnowCommand(unknown: true)
            }
          }
        }
      }
    ''', [unknown_arg('unknown', 'doesKnowCommand', 'Dog', 4, 27),
          unknown_arg('unknown', 'doesKnowCommand', 'Dog', 9, 31)])