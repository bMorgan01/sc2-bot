from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI
from sc2.units import UnitTypeId


class MyBot(BotAI):
    async def on_step(self, iteration: int):
        if not self.townhalls and self.already_pending(UnitTypeId.COMMANDCENTER) == 0:
            if self.can_afford(UnitTypeId.COMMANDCENTER):
                await self.build(UnitTypeId.COMMANDCENTER, near=self.start_location)

        else:
            cmd = self.structures(UnitTypeId.COMMANDCENTER)[0]

            ideal_workers = 0
            all_ideal = True
            for u in self.all_units:
                ideal_workers += u.ideal_harvesters

                if u.ideal_harvesters != u.assigned_harvesters:
                    all_ideal = False

            if self.workers.amount + self.already_pending(UnitTypeId.SCV) < ideal_workers:
                if self.can_afford(UnitTypeId.SCV):
                    self.train(UnitTypeId.SCV, closest_to=cmd)
                elif not self.can_feed(UnitTypeId.SCV) and self.can_afford(UnitTypeId.SUPPLYDEPOT) and self.already_pending(UnitTypeId.SUPPLYDEPOT) == 0:
                    await self.build(UnitTypeId.SUPPLYDEPOT, near=cmd)

            if self.structures(UnitTypeId.BARRACKS).closer_than(10, cmd).amount + self.already_pending(UnitTypeId.BARRACKS) < 2:
                if self.can_afford(UnitTypeId.BARRACKS):
                    await self.build(UnitTypeId.BARRACKS, near=cmd)

            for b in self.structures(UnitTypeId.BARRACKS).closer_than(10, cmd):
                if b.is_idle:
                    if self.can_afford(UnitTypeId.REAPER):
                        self.train(UnitTypeId.REAPER, closest_to=cmd)
                    elif not self.can_feed(UnitTypeId.REAPER) and self.can_afford(UnitTypeId.SUPPLYDEPOT) and self.already_pending(UnitTypeId.SUPPLYDEPOT) == 0:
                        await self.build(UnitTypeId.SUPPLYDEPOT, near=cmd)

            for vg in self.vespene_geyser.closer_than(10, cmd):
                if self.can_afford(UnitTypeId.REFINERY):
                    drone = self.workers.closest_to(vg)
                    drone.build_gas(vg)

            if self.units(UnitTypeId.REAPER).closer_than(10, cmd).amount > 0 and self.units(UnitTypeId.REAPER).closer_than(10, cmd).amount % 10 == 0:
                for m in self.units(UnitTypeId.REAPER).closer_than(10, cmd):
                    m.attack(self.enemy_start_locations[0])

            if not all_ideal:
                await self.distribute_workers()


run_game(maps.get("Acropolis LE"), [
    Bot(Race.Terran, MyBot()),
    Computer(Race.Protoss, Difficulty.Medium)
], realtime=True)
