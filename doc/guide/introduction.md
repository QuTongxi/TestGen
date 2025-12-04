文档首先介绍了如何自定义 Hypothesis 数据库：实现 `ExampleDatabase` 接口（如 `SQLiteExampleDatabase`），至少要提供 `save`、`delete`，可选 `move`，并且可以通过 `_broadcast_change()`、`_start_listening()`、`_stop_listening()` 实现变更监听。随后列举了内置实现：内存版 `InMemoryExampleDatabase`、目录版 `DirectoryBasedExampleDatabase`、GitHub Actions 产物版 `GitHubArtifactDatabase`、Redis 版 `RedisExampleDatabase`，以及用于组合的包装器：`ReadOnlyDatabase`、`MultiplexedDatabase`、`BackgroundWriteDatabase` 等，展示如何将本地数据库与远程/共享数据库协同使用，并配合 GitHub Actions 和 `GITHUB_TOKEN` 做 CI 场景下的失败用例共享。

设置（settings）部分说明了如何用 `@settings` 控制单个测试、用 profile 控制整个测试套件，并支持通过环境变量或 pytest 命令行选择配置。重点介绍了：`max_examples`、`derandomize`、`database`、`verbosity`、`phases`、`stateful_step_count`、`report_multiple_bugs`、`suppress_health_check`、`deadline`、`print_blob`、`backend` 等属性，以及 `Phase`、`Verbosity`、profile 注册加载等机制。健康检查（HealthCheck）部分强调应谨慎关闭检查，列举了针对正确性和性能的各类检查（如 `filter_too_much`、`data_too_large`、`function_scoped_fixture` 等），并说明可以通过配置有选择地抑制。

策略（strategies）章节从基本策略 `none()`、`nothing()`、`just(value)` 和整数策略展开，详细介绍了 `floats()` 的参数与约束（值域、NaN、无穷、次正规数、端点开闭等），给出 `complex_numbers()` 的接口，并说明可用 `.map()` 对生成值进行简单变换（如将整数列表映射为有序列表）。关于筛选输入，系统对比 `.filter()` 与 `assume()`：前者作用于单一策略、适合简单条件，后者可以基于任意条件丢弃整个测试用例。建议优先使用 `.filter()` 提高效率，而对复杂关系（如 `a % b == 0`）使用 `assume()`；内置策略有时会隐式调用这些机制。文档说明 `max_examples` 是“成功示例数”的目标值，但会因搜索空间耗尽、频繁重试、发现失败用例而提前结束或增加额外执行；同时解释失败用例如何自动保存与重放。

一个重要主题是“域 vs 分布”：Hypothesis 区分“可生成的输入集合”（域）和“各输入出现概率”（分布），主张由库内部控制分布，以便更高效地发现未知 bug。建议用户尽量选用通用、宽松的域，只因性能需要才收缩范围。文档解释不向用户开放分布控制的原因（人类不擅长选分布、分布依赖代码与属性、实现细节需可演进等），并指出更复杂的分布控制可交给替代后端（如 hypofuzz）。Hypothesis 内部使用复杂、持续改进的默认分布专门用来“找 bug”，而非均匀或“真实”采样。

在 `@given` 与类型推断方面，文档说明 `@given` 是 Hypothesis 的主入口：可以接受多个位置和关键字参数，将普通函数转换为属性测试；可配合 `hypothesis.infer`（`...`）从类型注解推断策略，并与 `builds()` 的推断行为进行对比。随后引入 `@example`：用于添加显式示例（通常是已知失败用例），这些示例优先于随机数据执行；`@example` 还支持 `.xfail()` 标记预期失败和 `.via()` 记录示例来源。可重现性部分介绍了 `hypothesis.reproduce_failure` 用于重放特定失败，以及 `hypothesis.seed` 用于固定随机种子。辅助函数 `assume()`、`note()` 和 `event()` 分别用于过滤不符合条件的用例、在失败时附加调试信息、记录统计事件。定向属性测试（Targeted PBT）通过 `target()` 为每个示例提供“评分”，引导引擎集中搜索更易触发失败的区域，并配合 `settings` 做细粒度控制。

类型提示部分，介绍如何使用 `SearchStrategy[T]` 为返回策略的函数标注类型，并区分“策略对象本身”与“返回策略的函数”。特别强调 `@composite` 下的函数返回类型应该直接写生成值类型（如 `tuple[int, int]`），而非 `SearchStrategy[...]`。解释 `SearchStrategy` 的协变性（`B <: A` 则 `SearchStrategy[B] <: SearchStrategy[A]`），并用 `Animal`/`Dog` 例子说明其意义。

关于自定义策略，文档介绍使用辅助函数与 `@composite` 装饰器创建复杂生成逻辑，在示例中实现“列表元素和为 1”的策略 `sums_to_one`，以及带普通参数与仅限关键字参数的 `sums_to_n`。展示如何用 `@composite` 生成相互依赖的值（如递增整数对），并讨论将数据生成逻辑写在策略里（`@composite`）和写在测试里（`data()`）的差异：`data()` 更灵活，但会让测试签名和类型更难分析，一般推荐优先使用 `@composite`。另外介绍了动态识别 Hypothesis 测试的方式：通过工具函数 `is_hypothesis_test()` 或 pytest 自动添加的 `hypothesis` 标记。

基础教程部分给出 Hypothesis 简介与安装方法，展示了第一个整数测试示例，并说明 Hypothesis 默认生成约 100 个随机输入、与 pytest / unittest 兼容。随后通过一系列示例展示如何用 `@given` + 策略测试整数检查函数、选择排序、以及使用策略组合（`|`）生成既含整数又含浮点数的列表，并指出应通过 `floats(allow_nan=False)` 排除 `NaN`。还介绍如何为测试提供多个参数，以及何时适合采用属性测试：例如往返属性、替代传统参数化测试、验证优化实现与规范实现的等价性、金融交易的守恒等。

内部机制方面，文档介绍 `PrimitiveProvider` 接口及其 `lifetime` 属性，用于控制原语生成的生命周期，并描述 `avoid_realization`、`add_observability_callback`、`draw_boolean`/`draw_integer`/`draw_float`/`draw_string` 等方法，以及 `per_test_case_context_manager`、`realize`、`replay_choices`、`observe_test_case`、`observe_information_messages`、`on_observation` 等钩子，这些接口主要用于内部或高级扩展场景（如观察与回放失败用例、采集统计信息等）。

状态测试（Stateful tests）部分介绍了 `RuleBasedStateMachine` 与 `rule` 装饰器，解释 Bundles 的概念及其相对实例变量的优势（鼓励多次复用同一对象，放大状态相关 bug）。通过 `DatabaseComparison` 示例，展示如何并行操作真实数据库与内存模型，以比较行为一致性，并依靠 `save`、`delete`、`values_agree` 等规则发现差异。还介绍 `consumes`、`multiple` 等辅助函数、`initialize` 用于初始化状态、`precondition` 声明前置条件、`invariant` 声明不变量，以及 `run_state_machine_as_test()` 将状态机作为测试运行的方式。

异常与 Flaky 行为部分系统列举了 Hypothesis 自定义异常：如 `InvalidArgument`、`ResolutionFailed`、`Unsatisfiable`、`DeadlineExceeded` 等参数或性能相关错误，以及 `FlakyFailure`、`FlakyBackendFailure` 用于表示非确定性失败。文档解释了“Flaky failures”的含义（同一用例在重试中从失败变为通过），指出任何测试框架都可能遇到，但 Hypothesis 因为多次运行和收缩示例，更容易暴露这种问题。

外部模糊测试集成方面，文档介绍了 `fuzz_one_input` 接口，它允许绕过标准 Hypothesis 生命周期，将测试函数暴露为外部模糊器（如 python-afl、Atheris）的目标。通过示例展示 Hypothesis 生成合法 JSON 再交由 Atheris 驱动的代码处理，并指出原生 Atheris 难以高效生成结构化数据。建议结合 `atheris.instrument_all` 或 `atheris.instrument_imports` 提高覆盖率，并说明 `fuzz_one_input` 与 `@settings` 的交互及配合 `BackgroundWriteDatabase` 进行性能优化的方法。

Django 集成部分说明如何通过继承专用 TestCase + `@given` 测试 Django 应用，推荐避免使用 `TransactionTestCase` 以提升性能。介绍 `from_model()` 自动为模型生成数据，`register_field_strategy` 为自定义字段注册策略，以及使用 `flatmap()` 生成具有父子关系的模型实例；并讨论了 `MultiValueField`、自定义主键等场景的处理方式。

最后，文档简要介绍 Hypothesis Ghostwriter 工具，用于自动生成属性测试及其 CLI 用法；提示深入阅读内部文档前的注意事项；并介绍“自定义函数执行”（自定义 executor）功能：通过定义 `execute_example` 控制每个示例在特定执行环境中运行（例如统一的 setup/teardown、子进程隔离等）。文末概览了核心内置策略家族，涵盖整数、浮点、布尔、文本、列表、元组等，并说明常见的组合与使用方式。
