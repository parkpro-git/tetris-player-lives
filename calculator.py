import math
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.stdin.reconfigure(encoding="utf-8")


def calculate(expression: str) -> float:
    allowed = set("0123456789 +-*/.()%^eEabcdefghijklmnopqrstuvwxyzABCDFGHIJKLMNOPQRSTUVWXYZ_,")
    if not all(c in allowed for c in expression):
        raise ValueError("허용되지 않은 문자가 포함되어 있습니다.")

    expression = expression.replace("^", "**")
    result = eval(expression, {"__builtins__": {}}, {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log10,
        "ln": math.log,
        "pi": math.pi,
        "e": math.e,
        "abs": abs,
    })
    return result


def main():
    print("=" * 40)
    print("         Python 계산기")
    print("=" * 40)
    print("사용 가능한 연산: + - * / // % ^ ()")
    print("함수: sqrt, sin, cos, tan, log, ln, abs")
    print("상수: pi, e")
    print("종료하려면 'q' 또는 'quit' 입력")
    print("=" * 40)

    history = []

    while True:
        try:
            user_input = input("\n계산식 입력 > ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("q", "quit", "exit"):
                print("계산기를 종료합니다.")
                break

            if user_input.lower() == "history":
                if not history:
                    print("계산 기록이 없습니다.")
                else:
                    print("\n[계산 기록]")
                    for i, (expr, res) in enumerate(history, 1):
                        print(f"  {i}. {expr} = {res}")
                continue

            if user_input.lower() == "clear":
                history.clear()
                print("기록을 초기화했습니다.")
                continue

            result = calculate(user_input)

            if isinstance(result, float) and result.is_integer():
                result_str = str(int(result))
            else:
                result_str = f"{result:.10g}"

            print(f"  = {result_str}")
            history.append((user_input, result_str))

        except ZeroDivisionError:
            print("  오류: 0으로 나눌 수 없습니다.")
        except ValueError as e:
            print(f"  오류: {e}")
        except SyntaxError:
            print("  오류: 잘못된 수식입니다.")
        except Exception as e:
            print(f"  오류: {e}")


if __name__ == "__main__":
    main()
