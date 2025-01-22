# 非同期処理をConnectionManagerに委譲
            future = asyncio.run_coroutine_threadsafe(
                self.manager.request_action(self.client_id, selection),
                self.manager.event_loop,
            )

            # 選択結果を待機
            selected_index = future.result(timeout=30)
