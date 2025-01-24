### どうリバースするか問題
### ジャローダどうするか問題
### 多種多様な攻撃どう実現するか問題

### online play めっちゃむずい問題

1. gameモジュールはawaitableじゃない一方で、入出力を求めている
  -> fastapiと相性が悪すぎる

Evaluating: future.result(timeout=10) did not finish after 3.00 seconds.
This may mean a number of things:
- This evaluation is really slow and this is expected.
    In this case it's possible to silence this error by raising the timeout, setting the
    PYDEVD_WARN_EVALUATION_TIMEOUT environment variable to a bigger value.

- The evaluation may need other threads running while it's running:
    In this case, it's possible to set the PYDEVD_UNBLOCK_THREADS_TIMEOUT
    environment variable so that if after a given timeout an evaluation doesn't finish,
    other threads are unblocked or you can manually resume all threads.

    Alternatively, it's also possible to skip breaking on a particular thread by setting a
    `pydev_do_not_trace = True` attribute in the related threading.Thread instance
    (if some thread should always be running and no breakpoints are expected to be hit in it).

- The evaluation is deadlocked:
    In this case you may set the PYDEVD_THREAD_DUMP_ON_WARN_EVALUATION_TIMEOUT
    environment variable to true so that a thread dump is shown along with this message and
    optionally, set the PYDEVD_INTERRUPT_THREAD_TIMEOUT to some value so that the debugger
    tries to interrupt the evaluation (if possible) when this happens.
